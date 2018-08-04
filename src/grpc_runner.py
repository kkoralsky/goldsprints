import site
import grpc
import sys
import time
from concurrent import futures
import traceback
import os

site.addsitedir("src")

from protos import sprints_pb2 as pb2
from protos import sprints_pb2_grpc as pb2_grpc
import visualize


RESOLUTION = map(int, os.environ.get("PYGAME_RESOLUTION", "640x480").split("x"))
FULLSCREEN = os.environ.has_key("PYGAME_FULLSCREEN")
UNIT = float(os.environ.get("PYGAME_UNIT", ".5"))
SAMPLING = float(os.environ.get("PYGAME_SAMPLING", "0.04"))
ROLLER_CIRCUM = .00025

class GrpcVisualizer(pb2_grpc.VisualServicer):
    DISTANCE = 0
    TIME = 1
    def __init__(self, vis_instance):
        self.vis = vis_instance

    def _dist_not_finished(self, dist):
        if self.mode is self.DISTANCE:
            return dist < self.dist
        return True

    def NewTournament(self, request, context):
        self.player_count = request.playerCount
        self.mode = request.mode
        self.colors = request.color
        self.vis.set_dist(request.destValue)

    def NewRace(self, request, context):
        self.player_names = [p.name for p in request.players]
        self.player_count = len(self.player_names)
        self.dist = request.destValue
        self.vis.set_dist(request.destValue)
        self.vis.new_race(self.player_names)

    def StartRace(self, request, context):
        self.vis.start([True]*2)

    def AbortRace(self, request, context):
        self.vis.banner(request.message)

    def UpdateRace(self, request_iterator, context):
        start_time=time.time()
        between_time=[start_time,start_time]
        avg_between_time = [start_time, start_time]
        avg_between_dist = [0, 0]
        between_dist=[0,0]
        curr_dist=[0,0]
        speed=[0,0]
        bars = self.mode==self.DISTANCE

        for req in request_iterator:
            p = req.playerNum
            dist = req.distance
            curr_time = time.time()
            dtime = curr_time-between_time[p]
            if dtime > SAMPLING:
                curr_dist[p] = dist
                dpos = curr_dist[p]-between_dist[p]
                if dpos>0 and self._dist_not_finished(between_dist[p]):
                    if curr_time-avg_between_time[p] > 1:  # upd speed every sec
                        speed[p] = 3600*ROLLER_CIRCUM*UNIT*(curr_dist[p]-avg_between_dist[p])/(curr_time-avg_between_time[p])
                        avg_between_time[p] = curr_time
                        avg_between_dist[p] = curr_dist[p]

                    self.vis.update_race(p, dist, dpos, speed[p], curr_time-start_time, bars=bars)
                    between_dist[p]=curr_dist[p]
                between_time[p]=curr_time

    def FinishRace(self, request, context):
        try:
            name_ord_map = { name: i for i, name in enumerate(self.player_names) }
            results = [None]*self.player_count
            for r in request.result:
                # [result, name, current position]
                results[name_ord_map[r.player.name]] = [(r.result * 10**-3) if self.mode==self.DISTANCE else r.result,
                                                        r.player.name, 0]
            self.vis.finish(results)
        except Exception:
            traceback.print_exc()


class GrpcRunner(object):
    def __init__(self, vis_name="simplegame", port=9998):
        self.port = port
        vis_class = getattr(visualize, vis_name.capitalize() + "Vis")
        self.vis = vis_class(RESOLUTION, fullscreen=FULLSCREEN, unit=UNIT)

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
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
