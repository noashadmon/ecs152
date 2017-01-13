# This is a simpy based  simulation of a M/M/1 queue system

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 1000000
MU = 1
currSlot = 0
totPkts = 0
#slotTargetNum = S
#total_no_packets = L

""" Queue system  """       
class server_queue:
    def __init__(self, env, arrival_rate):
        self.server = simpy.Resource(env, capacity = 1)
        self.env = env
        #self.queue_len = 0
        self.N = 0 #times head packet was retransmitted
        self.S = 1 #slot num of next transmisssion
        self.L = 0 #num packets in queue
        self.queue_len = 0
        self.process = 0
        
        
        self.arrival_rate = arrival_rate
        
    def process_packt(self, env):
        global currSlot, totPkts
        self.queue_len -= 1 #pkt has been processed remove one from q
        totPkts += 1 #one more pkt has been processed

        if self.queue_len == 0:
            self.process = 0 #no packets in queue then no packets processed
        elif self.queue_len > 0:
            self.N = 1
            self.S = currSlot + 1 #move on to next slot
            self.process = 1
    def packets_arrival(self, env):
        with True:
            yield env.timeout(random.expovariate(self.arrival_rate))
            #print("Packet number {0} with arrival time {1} latency {2}".format(packet.identifier, packet.arrival_time, latency))
            self.L += 1
            self.queue_len += 1
            #check to see if queue had first packet arrive
            if self.process == 0:
                self.process = 1
                self.N = 1
                self.S = currSlot + 1
    
                
    
""" Ethernet class """          
class ethernet:
    def __init__(self, env, host):
        self.env = env
        self.host = host
        self.currSlotloc = 1
        self.pktProcess = 0
        self.failure = 0 #if collisiojn

        [env.process(self.host[i].packets_arrival(self.env)) for i in range(10)]


    #binary exp
    def binExp(self, env):
        global currSlot
        while True:
            slots = []
            for i in range(10):
                                #if the host wants to process a pkt in the current slot
                if ((self.host[i].process == 1) and (self.host[i].S <= currSlot)):
                    self.host[i].S = currSlot
                    slots.append(i)
                        #calculates future slot if there is a collision
            for j in slots:
                self.expBackoff(self.host[j])
                self.failure = self.failure+1

                        #process packet in slot
            if len(slots) == 1:
                self.host[slots[0]].process_packet(env)

                        #update slot
            #currSlot += 1

                        #timeout when hit service time of 1 sec
            yield env.timeout(1)
            currSlot += 1
    def expBackoff(self, host):
        k = min(host.N, 10)
        num = random.randint(0, 2**k)
        host.S += num
        host.N += 1

    def linBackoff(self, env):
        global currSlot, totPkts
        while True:
            slots = []
            for i in range(10):
                                #if the host wants to process a pkt in the current slot
                if ((self.host[i].process == 1) and (self.host[i].S <= currSlot)):
                    self.host[i].S = currSlot
                    slots.append(i)
                        #calculates future slot if there is a collision
            for i in slots:
                self.linBack(self.host[i])
                self.failure = self.failure+1

                        #process packet in slot
            if len(slots) == 1:
                self.host[slots[0]].process_packet(env)

                        #update slot
            currSlot += 1

                        #timeout when hit service time of 1 sec
            yield env.timeout(1)
    def linBack(self, host):
        k = min(host.N, 1024)
        num = random.randint(0, k)
        host.S += num
        host.N -= 1



def main():
    global currSlot, totPkts
    random.seed(RANDOM_SEED)

    print("Binary Exponential Backoff Model with 10 Queues, for slot time of 1 and 10 hosts: ")
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        print ("{0:<15} {1:<15} {2:<17} {3:<15} {4:<15}".format(
                "Lambda", "TotalSlots","ProcessedPackets","Throughput","PacketSlotCollisions"))
        currSlot = 0
        totPkts= 0
        env = simpy.Environment()
        queues = [server_queue(env, arrival_rate) for j in range(10)]
        router = ethernet(env, queues)
        env.process(router.binExp(env))
        print "hi"
        env.run(until=SIM_TIME)
        print ("{0:<1.2f} {1:<10} {2:<15} {3:<17} {4:<2.5f} {5:<7} {6:<15}".format(
                float(arrival_rate),
                "",
                int(currSlot),
                int(totPkts),
                float(float(totPkts)/currSlot),
                "",
                ))









'''
    global currSlot, totPkts
    print("Binary Exponential Backoff Model for 10 Hosts")
    #print ("{0:<9} {1:<9} {2:<9} {3:<9} {4:<9} {5:<9} {6:<9} {7:<9}".format(
        #"Lambda", "Count", "Min", "Max", "Mean", "Median", "Sd", "Utilization"))
    random.seed(RANDOM_SEED)
    print "hi"
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07,.08,0.09]:
        env = simpy.Environment()
        currSlot = 0
        totPkts = 0
        host = [server_queue(env, arrival_rate) for k in range(10)]
        router = ethernet(env, host)
        env.process(router.binExp(env))
        env.run(until=SIM_TIME)
        print "hello"
        print ("{0:<9.3f}{1:<9.5f}".format(
                arrival_rate,
                totPkts/currSlot))
    print "Linear Backoff Model for 10 Hosts"
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07,.08,0.09]:
        env = simpy.Environment()
        currSlot = 0
        totPkts = 0
        host = [server_queue(env, arrival_rate) for i in range(10)]
        router = ethernet(env, host)
        env.process(router.linBackoff(env))
        env.run(until=SIM_TIME)
        print ("{0:<9.3f}{1:<9.5f}".format(
                arrival_rate,
                totPkts/currSlot))  
'''    
if __name__ == '__main__': main()




