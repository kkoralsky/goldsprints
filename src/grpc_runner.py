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
        pass

    def NewRace(self, request, context):
        self.vis.new_race([p.name for p in request.players])

    def StartRace(self, request, context):
        pass
    def AbortRace(self, request, context):
        pass
    def UpdateRace(self, request_iterator, context):
        pass
    def FinishRace(self, request, context):
        pass


class GrpcRunner(object):
    default_port = 9998

    def __init__(self, vis_name="simplegame", port=None):
        self.port = self.default_port if port is None else port
        vis_class = getattr(visualize, vis_name.capitalize()+"Vis")
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
    GrpcRunner(vis_name=sys.argv[1], port=int(sys.argv[2])).serve()
