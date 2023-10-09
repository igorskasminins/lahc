import yaml
import random
from ast import literal_eval

TEST_CASE = 'test3'

with open('config.yaml', 'r') as file:
    prime_service = yaml.safe_load(file)
    matrix = literal_eval(prime_service[TEST_CASE])

class WrongActionException(Exception):
    """ Exception for the impossible move that is being/was performed in a route """
    def __init__(self, message='Wrong action'):
        super(WrongActionException, self).__init__(message)

class Vehicle:
    """ A vehicle with containers """
    empty_containers = 0
    full_containers = 0
    current_position = 0

    def deliver_empty(self):
        """ Give to the client an empty container """
        self.empty_containers -= 1

    def take_full(self):
        """ Take a full container from the client """
        self.full_containers += 1

    def replace(self):
        """ Empty full containers """
        self.empty_containers += self.full_containers
        self.full_containers = 0

class Solution:
    """ The solution of the problem that consists of a vehicle and a list of ordered clients to be visited """
    cost = 0
    vehicle = None
    test_mode = False
    result = []
    possible_swaps = []

    def __init__(self):
        self.vehicle = Vehicle()
        self.clients = [i for i in range(1, len(matrix))]
        self.clients_need_pickup = self.clients.copy()
        self.clients_need_containers = []

    def go_dump(self):
        """ Return to the dump, and empty containers """
        if not self.test_mode:
            self.result.append(0)

        self.vehicle.replace()
        self.cost += matrix[self.vehicle.current_position][0]
        self.vehicle.current_position = 0

    def go_pickup_client(self, pickup_client = None):
        """
        Go to the client who needs their full container to be taken

        If no pickup client is provided to go to, one is randomly being taken from the available pool
        """

        if self.vehicle.full_containers == 2 or self.vehicle.empty_containers == 2 or (self.vehicle.empty_containers == 1 and self.vehicle.full_containers == 1):
            self.cost = -1
            raise WrongActionException

        if pickup_client == None:
            pickup_client = random.choice(self.clients_need_pickup)

        if not self.test_mode:
            self.result.append(pickup_client)

        self.cost += matrix[self.vehicle.current_position][pickup_client]
        self.vehicle.current_position = pickup_client
        self.vehicle.take_full()
        self.clients_need_pickup.remove(pickup_client)
        self.clients_need_containers.append(pickup_client)

        return pickup_client

    def go_needy_client(self, needy_client = None):
        """ 
        Go to the client who needs an empty container

        If no client that needs a container is provided to go to, one is randomly being taken from the available pool
        """
        if self.vehicle.empty_containers == 0:
            self.cost = -1
            raise WrongActionException
        
        if needy_client == None:
            needy_client = random.choice(self.clients_need_containers)

        if not self.test_mode:
            # If the result is being generated add it to the resulting path
            self.result.append(needy_client)

        self.cost += matrix[self.vehicle.current_position][needy_client]
        self.vehicle.current_position = needy_client
        self.vehicle.deliver_empty()
        self.clients_need_containers.remove(needy_client)

    def generate_default_solution(self):
        """ Generate a random solution """
        # The solution always starts with the vehicle beeing at the beginning
        self.result = [0]

        while len(self.clients_need_pickup) | len(self.clients_need_containers):
            # Handle each possible case, in which the vehicle can appear, separately (based on containers)
            if self.vehicle.empty_containers == 0 and self.vehicle.full_containers == 0:
                # only find clients (the truck has no continaers => must take from the clients)
                self.go_pickup_client()
            elif self.vehicle.empty_containers == 0 and self.vehicle.full_containers == 2:
                # only go the dump (nobody needs full containers)
                self.go_dump()
            elif self.vehicle.empty_containers == 2 and self.vehicle.full_containers == 0:
                # only find a client
                self.go_needy_client()
            elif self.vehicle.empty_containers == 0 and self.vehicle.full_containers == 1:
                # can either go to the dump or take a full contaienr
                if len(self.clients_need_pickup) == 0:
                    self.go_dump()
                    continue

                rand_branch = random.randint(0, 1)
                if rand_branch == 0:
                    self.go_dump()
                else:
                    self.go_pickup_client()

            elif self.vehicle.empty_containers == 1 and self.vehicle.full_containers == 0:
                # can either take a full contaier or deliver an empty container
                if len(self.clients_need_pickup) == 0:
                    self.go_needy_client()
                    continue

                if len(self.clients_need_containers) == 0:
                    self.go_pickup_client()
                    continue

                rand_branch = random.randint(0, 1)
                # Can either to a client that has full or needs an empty container
                if rand_branch == 0:
                    self.go_pickup_client()
                else:
                    self.go_needy_client()
            elif self.vehicle.empty_containers == 1 and self.vehicle.full_containers == 1:
                # can either go to the dump or deliver an empty continaer
                if len(self.clients_need_containers) == 0:
                    self.go_dump()
                    continue

                rand_branch = random.randint(0, 1)
                # Can either go to the dump or deliver an empty container
                if rand_branch == 0:
                    self.go_dump()
                else:
                    self.go_needy_client()

        # Always return to the dump at the end
        self.go_dump()

        return self.result
    
    def get_cost(self):
        """ Get the total cost of current solution """
        return self.cost
    
    def swap(self, swap_positions = None):
        """ Swap provided elements by indexes of the resulting list - randomly if not provided  """
        if len(self.possible_swaps) == 0:
            return -1
        
        if swap_positions == None:
            swap_positions = random.choice(self.possible_swaps)

        # exclude the performed swap from the available pool of swaps
        self.possible_swaps.remove(swap_positions)
        x = self.result[swap_positions[0]]
        self.result[swap_positions[0]] = self.result[swap_positions[1]]
        self.result[swap_positions[1]] = x
        
    def verify_cost(self):
        """ Verify the legitimacy of current solution and retrieve the total costs """
        # Reset values for cases when the previous swap was incorrect
        self.test_mode = True
        self.cost = 0
        self.vehicle.empty_containers = 0
        self.vehicle.full_containers = 0
        self.clients_need_pickup = self.clients.copy()
        self.clients_need_containers = []

        for cell in self.result:
            if cell == 0:
                self.go_dump()

            elif cell in self.clients_need_pickup:
                self.go_pickup_client(cell)

            elif cell in self.clients_need_containers:
                self.go_needy_client(cell)
                
        self.clients_need_containers = []
        self.clients_need_pickup = self.clients.copy()

        return self.cost

def find_all_pairs(lst):
   """ Generate allowed pairs of elements that could be replaced - excludes the dump """
   pairs = []
   for i in range(1, len(lst) -1):
      for j in range(i + 1, len(lst) -1):
        pairs.append((i, j))
   return pairs

def lahc():
    """ Late Accaptance Hill Climbing algorithm """
    # Keep track of the best possible solution
    best_solution = solution = Solution()
    best_solution.generate_default_solution()
    print('Original Path:\t', solution.result)
    print('Original Cost:\t', solution.cost)
    possible_swaps = find_all_pairs(solution.result)

    best_solution.possible_swaps = possible_swaps
    solution.possible_swaps = possible_swaps

    existing_combinations = [solution.result.copy()]
    cost = best_solution.get_cost()
    n = [cost for _ in range(1000)]
    exit = False

    while True:
        # Generate default solution
        new_solution = Solution()
        new_solution.result = solution.result.copy()
        new_solution.possible_swaps = solution.possible_swaps.copy()

        # Perform the first swap of clients
        new_solution.swap()

        while True:
            try:
                # Verify that the swap of clients is possible
                cost = new_solution.verify_cost()

                # Skip duplicate results
                if len(new_solution.possible_swaps) and (new_solution.result in existing_combinations):
                    
                    new_solution.result = solution.result.copy()
                    new_solution.swap()
                    continue

                # No new actions can be done - exit
                elif not len(new_solution.possible_swaps):
                    exit = True
                else:
                    existing_combinations.append(new_solution.result)

            except WrongActionException:
                # An impossible swap has been made - perform a different swap
                new_solution.result = solution.result.copy()
                new_solution.swap()

                continue

            if cost < n[-1]:
                # Save the new better result based on the last outcome from the stack
                solution = new_solution
                solution.possible_swaps = possible_swaps.copy()

            if cost < best_solution.cost:
                best_solution = solution

            # Save the result to the stack and remove the last value
            n.insert(0, cost)
            n.pop()

            break
        # Esxit the execution once no more new swaps can be made
        if exit == True:
            break

    print('Final Path:\t', best_solution.result)
    print('Final Cost:\t', best_solution.verify_cost())

lahc()
