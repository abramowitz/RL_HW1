import numpy as np
from cartpole_cont import CartPoleContEnv
import matplotlib.pyplot as plt


def get_A(cart_pole_env):
    '''
    create and returns the A matrix used in LQR. i.e. x_{t+1} = A * x_t + B * u_t
    :param cart_pole_env: to extract all the relevant constants
    :return: the A matrix used in LQR. i.e. x_{t+1} = A * x_t + B * u_t
    '''
    g = cart_pole_env.gravity
    pole_mass = cart_pole_env.masspole
    cart_mass = cart_pole_env.masscart
    pole_length = cart_pole_env.length
    dt = cart_pole_env.tau


    A= np.matrix([
        [1, dt, 0                                          , 0 ],
        [0, 1 , (pole_mass/cart_mass)*g*dt                 , 0 ],
        [0, 0 , 1                                          , dt],
        [0, 0 , (g/pole_length)*(1+pole_mass/cart_mass)*dt , 1 ]
    ])
    return A


def get_B(cart_pole_env):
    '''
    create and returns the B matrix used in LQR. i.e. x_{t+1} = A * x_t + B * u_t
    :param cart_pole_env: to extract all the relevant constants
    :return: the B matrix used in LQR. i.e. x_{t+1} = A * x_t + B * u_t
    '''
    g = cart_pole_env.gravity
    pole_mass = cart_pole_env.masspole
    cart_mass = cart_pole_env.masscart
    pole_length = cart_pole_env.length
    dt = cart_pole_env.tau

    B = np.matrix([
        [0],
        [dt/cart_mass],
        [0],
        [dt/(cart_mass*pole_length)]
    ])

    return B


def find_lqr_control_input(cart_pole_env):
    '''
    implements the LQR algorithm
    :param cart_pole_env: to extract all the relevant constants
    :return: a tuple (xs, us, Ks). xs - a list of (predicted) states, each element is a numpy array of shape (4,1).
    us - a list of (predicted) controls, each element is a numpy array of shape (1,1). Ks - a list of control transforms
    to map from state to action, np.matrix of shape (1,4).
    '''
    assert isinstance(cart_pole_env, CartPoleContEnv)

    # TODO - you first need to compute A and B for LQR
    A = get_A(cart_pole_env)
    B = get_B(cart_pole_env)

    # TODO - Q and R should not be zero, find values that work, hint: all the values can be <= 1.0
    Q = np.matrix([
        [0.5, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0.3, 0],
        [0, 0, 0, 0]
    ])

    R = np.matrix([0.2])

    # TODO - you need to compute these matrices in your solution, but these are not returned.
    # TODO - these should be returned see documentation above

    Ps = []
    us = []
    xs =[np.expand_dims(cart_pole_env.state,1)]
    Ks = []
    Ps=[Q]

    for i in range(cart_pole_env.planning_steps):
        Temp1=A.T*Ps[0]*B
        Temp2=(R+B.T*Ps[0]*B).I
        Temp3 =B.T*Ps[0]* A

        ps1=np.matrix(Q+A.T*Ps[0]*A-Temp1*Temp2*Temp3)
        Ps.insert(0,ps1)


    for i in range(cart_pole_env.planning_steps):
        Temp2 = (R + B.T * Ps[i+1] * B).I
        Temp3 = B.T * Ps[i+1] * A

        Ks.append(np.matrix(-Temp2*Temp3))
        us.append(np.matrix(Ks[i]*xs[i]))
        xs.append(np.matrix(A*xs[i]+B*us[i]))


    assert len(xs) == cart_pole_env.planning_steps + 1, "if you plan for x states there should be X+1 states here"
    assert len(us) == cart_pole_env.planning_steps, "if you plan for x states there should be X actions here"
    for x in xs:
        assert x.shape == (4, 1), "make sure the state dimension is correct: should be (4,1)"
    for u in us:
        assert u.shape == (1, 1), "make sure the action dimension is correct: should be (1,1)"
    return xs, us, Ks

def print_diff(iteration, planned_theta, actual_theta, planned_action, actual_action):
    print('iteration {}'.format(iteration))
    print('planned theta: {}, actual theta: {}, difference: {}'.format(
        planned_theta, actual_theta, np.abs(planned_theta - actual_theta)
    ))
    print('planned action: {}, actual action: {}, difference: {}'.format(
        planned_action, actual_action, np.abs(planned_action - actual_action)
    ))



if __name__ == '__main__':
    fig, ax = plt.subplots()
    for theta4 in [0.36 , 0.1, 0.36*0.5]:
        env = CartPoleContEnv(initial_theta=np.pi * theta4)
        # the following is an example to start at a different theta
        # env = CartPoleContEnv(initial_theta=np.pi * 0.25)
        print(env)
        # print the matrices used in LQR
        print('A: {}'.format(get_A(env)))
        print('B: {}'.format(get_B(env)))

        # start a new episode
        actual_state = env.reset()
        env.render()
        # use LQR to plan controls
        xs, us, Ks = find_lqr_control_input(env)
        # run the episode until termination, and print the difference between planned and actual
        is_done = False
        iteration = 0
        is_stable_all = []
        theta=[]

        while not is_done:

            # print the differences between planning and execution time
            predicted_theta = xs[iteration].item(2)
            actual_theta = actual_state[2]
            predicted_action = us[iteration].item(0)
            theta.append(actual_theta-np.pi*int(actual_theta/np.pi))
            actual_action = (Ks[iteration] * np.expand_dims(actual_state, 1)).item(0)
            print_diff(iteration, predicted_theta, actual_theta, predicted_action, actual_action)
            # apply action according to actual state visited
            # make action in range
            actual_action = max(env.action_space.low.item(0), min(env.action_space.high.item(0), actual_action))
            actual_action = np.array([actual_action])
            actual_state, reward, is_done, _ = env.step(actual_action.astype(np.float32))
            is_stable = reward == 1.0
            is_stable_all.append(is_stable)
            env.render()
            iteration += 1
        env.close()
        # we assume a valid episode is an episode where the agent managed to stabilize the pole for the last 100 time-steps
        valid_episode = np.all(is_stable_all[-100:])
        # print if LQR succeeded

        print('valid episode: {}'.format(valid_episode))
        # print(theta)
        dt_array=0.01*np.arange(0, 600)
        #print(dt_array)


        ax.plot(dt_array,theta )
    ax.set(xlabel='time (s)', ylabel='theta (rad))',
           title='theta over time')
    ax.grid()
    plt.legend(["theta unstable=0.36pi","theta=0.1pi","theta unstable*0.5=0.18pi"])
    plt.show()
