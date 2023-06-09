from puzzle import *
from planning_utils import *
import heapq
import datetime


def a_star(puzzle):
    '''
    apply a_star to a given puzzle
    :param puzzle: the puzzle to solve
    :return: a dictionary mapping state (as strings) to the action that should be taken (also a string)
    '''

    # general remark - to obtain hashable keys, instead of using State objects as keys, use state.as_string() since
    # these are immutable.

    initial = puzzle.start_state
    goal = puzzle.goal_state

    # this is the heuristic function for of the start state
    initial_to_goal_heuristic = initial.get_manhattan_distance(goal)

    # the fringe is the queue to pop items from
    fringe = [(initial_to_goal_heuristic, initial)]
    # concluded contains states that were already resolved
    concluded = set()
    # a mapping from state (as a string) to the currently minimal distance (int).
    distances = {initial.to_string(): 0}
    # the return value of the algorithm, a mapping from a state (as a string) to the state leading to it (NOT as string)
    # that achieves the minimal distance to the starting state of puzzle.
    prev = {initial.to_string(): None}
    # i = 0

    while len(fringe) > 0:
        # remove the following line and complete the algorithm
        # assert False
        _, u = heapq.heappop(fringe)
        if u.to_string() in concluded:
            continue
        if u.is_same(goal):
            break
        concluded.add(u.to_string())
        for a in u.get_actions():
            # i+=1
            v = u.apply_action(a)
            if v.to_string() not in distances or distances[v.to_string()] > distances[u.to_string()] + 1:
                distances[v.to_string()] = distances[u.to_string()] + 1
                prev[v.to_string()] = u
                heapq.heappush(fringe, (distances[v.to_string()] + v.get_manhattan_distance(goal)*1, v))
                # heapq.heappush(fringe, (distances[v.to_string()] + v.get_incorrect_tiles_distance(goal), v))
    # print(i)
    return prev


def solve(puzzle):
    # compute mapping to previous using dijkstra
    prev_mapping = a_star(puzzle)
    # extract the state-action sequence
    plan = traverse(puzzle.goal_state, prev_mapping)
    print_plan(plan)
    return plan


if __name__ == '__main__':
    # we create some start and goal states. the number of actions between them is 25 although a shorter plan of
    # length 19 exists (make sure your plan is of the same length)
    initial_state = State()
    # import os
    # initial_state = State("0 7 6" + os.linesep + "5 3 4" + os.linesep + "2 1 8")
    actions = [
        'r', 'r', 'd', 'l', 'u', 'l', 'd', 'd', 'r', 'r', 'u', 'l', 'd', 'r', 'u', 'u', 'l', 'd', 'l', 'd', 'r', 'r',
        'u', 'l', 'u'
    ]
    goal_state = initial_state
    for a in actions:
        # goal_state = State()
        goal_state = goal_state.apply_action(a)
    puzzle = Puzzle(initial_state, goal_state)
    print('original number of actions:{}'.format(len(actions)))
    solution_start_time = datetime.datetime.now()
    solve(puzzle)
    print('time to solve {}'.format(datetime.datetime.now()-solution_start_time))
