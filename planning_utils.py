def traverse(goal_state, prev):
    '''
    extract a plan using the result of dijkstra's algorithm
    :param goal_state: the end state
    :param prev: result of dijkstra's algorithm
    :return: a list of (state, actions) such that the first element is (start_state, a_0), and the last is
    (goal_state, None)
    '''
    result = [(goal_state, None)]
    # remove the following line and complete the algorithm
    # assert False
    prev_state = prev[goal_state.to_string()]
    next_state = goal_state.copy()
    while prev_state is not None:
        for action in prev_state.get_actions():
            if prev_state.apply_action(action).is_same(next_state):
                result.append((prev_state,action))
        next_state = prev_state.copy()
        prev_state = prev[prev_state.to_string()]
    result = list(reversed(result))
    return result


def print_plan(plan):
    print('plan length {}'.format(len(plan)-1))
    for current_state, action in plan:
        print(current_state.to_string())
        if action is not None:
            print('apply action {}'.format(action))
