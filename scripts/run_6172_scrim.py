#!/usr/bin/env python

'''
Description:
Queues scrimmage games on scrimmage.csail.mit.edu without
uploading binaries (expects the binaries to be already uploaded).

Author:
Matthew Feng, mattfeng@mit.edu
'''

import argparse
import getpass
import uuid
import subprocess

from pyleiser.util import error, info

# Amazon S3 bucket name.
student_bucket = '6172-test-filesystem'

# Key prefix for user folders in bucket.
object_key_prefix = 'userhome'

# Key folder for game lists to be tested.
object_key_tests = 'autotest_test_uploads'

# Server for submitting autotests.
submit_server = 'cloud9.csail.mit.edu:4040'

TIME_CONTROL_MAP = {
    'blitz': {
        'tc_inc': 0.5,
        'tc_pool': 60
    },
    'blitz2': {
        'tc_inc': 1.0,
        'tc_pool': 60
    },
    'regular': {
        'tc_inc': 2,
        'tc_pool': 120
    },
    'regular2': {
        'tc_inc': 1,
        'tc_pool': 180
    },
    'long': {
        'tc_inc': 10,
        'tc_pool': 480
    }
}

def parse_player_name(name):
    if name.find('#') == -1:
        return name, 1.0
    
    base = name.split('#')[0]
    mult = name.split('#')[1]

    return base, float(mult)

def round_robin(players, time_control, round_robin_rounds, username):
    # Get the list of uploaded binaries
    pipe = subprocess.Popen(['autotest-list', '10000'], stdout = subprocess.PIPE, universal_newlines = True)
    staff_binaries = set(['reference', 'reference_plusplus'])
    binaries = set()

    output = pipe.communicate()[0]
    for line in output.split('\n'):
        player = line.split(' ')[0]

        if player.startswith(username):
            binaries.add(player)
    
    all_binaries = staff_binaries.union(binaries)

    info('All available competitors (add #<number> to multiply total time, e.g. reference*4 has 4x time): ')
    for binary in binaries:
        info('* {}'.format(binary))
    
    for i in range(0, len(players)):
        if players[i] not in staff_binaries and not players[i].startswith(username):
            players[i] = '{}.{}'.format(username, players[i])
    
    for p in players:
        base_p, _ = parse_player_name(p)
        if base_p not in all_binaries:
            error('Bot `{}` has not been uploaded to the 6.172 server.'.format(p))
            exit(1)

    # No need to modify anything below this line.
    autotest_filename = '/tmp/tmp.6172_autotest-{}'.format(uuid.uuid4())
    with open(autotest_filename, 'w') as f:
        f.write('***Manual Game List***\n')
        f.write('{}.\n'.format(username))

        tc_inc  = TIME_CONTROL_MAP[time_control]['tc_inc']
        tc_pool = TIME_CONTROL_MAP[time_control]['tc_pool']

        # Schedule round robin rounds
        for i in range(round_robin_rounds):
            for p1 in players:
                for p2 in players:
                    # Set up time multipliers.
                    p1_base, p1_mul = parse_player_name(p1)
                    p2_base, p2_mul = parse_player_name(p2)

                    if p1_base == p2_base:
                        continue

                    game_str = '{} {} {} {} true {} {}'.format(
                        p1_base, p2_base,
                        int(tc_pool * p1_mul), tc_inc * p1_mul,
                        int(tc_pool * p2_mul), tc_inc * p2_mul
                    )

                    info('Queuing game: {}'.format(game_str))
                    f.write('{}\n'.format(game_str))

    subprocess.call(['autotest-lowlevelrun', autotest_filename])

def get_user():
    try:
        athena_user = str(getpass.getuser())
    except Exception as e:
        error('Could not get student username.')
        print(e)
        exit(1)
    
    info('Found username `{}`.'.format(athena_user))
    
    return athena_user

def main(time_control, rounds, players):
    username = get_user()
    round_robin(players, time_control, rounds, username)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('time_control',
        help = 'time control mode to play',
        choices = TIME_CONTROL_MAP.keys(),
        type = str
        )

    parser.add_argument('rounds',
        help = 'number of round robin rounds to play',
        type = int
        )

    parser.add_argument('players',
        help = 'list of players to participate in the round robin',
        nargs = '+',
        type = str
        )
    
    args = parser.parse_args()

    main(
        time_control = args.time_control,
        rounds = args.rounds,
        players = args.players
        )
