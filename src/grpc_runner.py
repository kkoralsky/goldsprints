import site
import grpc
import sys
import time
from concurrent import futures
import os

site.addsitedir("src")

from protos import sprints_pb2 as pb2
from protos import sprints_pb2_grpc as pb2_grpc
import visualize


RESOLUTION=map(int, os.environ.get("PYGAME_RESOLUTION", "640x480").split("x"))
FULLSCREEN=os.environ.has_key("PYGAME_FULLSCREEN")
UNIT=int(os.environ.get("PYGAME_UNIT", "5"))


class GrpcVisualizer(pb2_grpc.VisualServicer):
    def __init__(self, vis_instance):
        self.vis = vis_instance

    def NewTournament(self, request, context):
        self.player_count = request.player_count
        self.mode = request.mode
        self.colors = request.color
        self.set_dist(request.destValue)

    def NewRace(self, request, context):
        self.player_names = [p.name for p in request.players]
        self.player_count = len(self.player_names)
        self.vis.new_race(self.player_names)

    def StartRace(self, request, context):
        self.vis.start([True]*2)

    def AbortRace(self, request, context):
        self.vis.banner(request.message)

    def UpdateRace(self, request_iterator, context):
        pass

    def FinishRace(self, request, context):
        # [name, result, current position]
        results = [[r.player.name, r.result, 0] for r in request.result]
        self.vis.finish(results)


class GrpcRunner(object):
    def __init__(self, vis_name="simplegame", port=9998):
        self.port = port
        vis_class = getattr(visualize, vis_name.capitalize() + "Vis")
        self.vis = vis_class(RESOLUTION, fullscreen=FULLSCREEN, unit=UNIT)

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_VisualServicer_to_server(
            GrpcVisualizer(self.vis), server)
        server.add_insecure_port('[::]:{}'.format(self.port))
        server.start()
        try:
            while True:
                time.sleep(60*60*24)
        except KeyboardInterrupt:
            server.stop(0)
            self.vis.quit()


if __name__ == '__main__':
    GrpcRunner(*sys.argv[1:]).serve()
