#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp.web
import addict
import time
import sys
import os
import json
import datetime
import argparse
import pprint

# default false, can be changed via program arguments (-v)
DEBUG_ON = False

# exit codes for shell, failre cones can be sub-devided
# if required and shell/user has benefit of this information
EXIT_OK      = 0
EXIT_FAILURE = 1


def err(msg):
    sys.stderr.write(msg)
    sys.exit(EXIT_FAILURE)

def warn(msg):
    sys.stderr.write(msg)


def debug(msg):
    if not DEBUG_ON: return
    sys.stderr.write(msg)


def debugpp(d):
    if not DEBUG_ON: return
    pprint.pprint(d, indent=2, width=200, depth=6)
    sys.stderr.write("\n")


def msg(msg):
    sys.stdout.write(msg)

def response_error(msg):
    response_data = {'status': 'failure', "message" : msg}
    body = json.dumps(response_data).encode('utf-8')
    return aiohttp.web.Response(body=body, content_type="application/json") 

async def http_ipc_handle_routes_add(request):
    if not request.has_body:
        return response_error("data has no JSON body")
    terminal = request.match_info['terminal']
    request_data = addict.Dict(await request.json())
    fmt = "received route changes for terminal {}\n"
    err(fmt.format(terminal))
    debugpp(request_data)
    response_data = {'status': 'ok'}
    body = json.dumps(response_data).encode('utf-8')
    return aiohttp.web.Response(body=body, content_type="application/json") 


async def http_ipc_handle_interfaces_get(request):
    terminal = request.match_info['terminal']
    if terminal not in ("term00", "term01"):
        return response_error("a valid terminal name is required")
    if terminal not in request.app["conf"]["interfaces_default_data"]:
        # a simple default value for now
        response_data = {'eth0': { "ip-addr": "192.168.1.1" } }
    response_data = request.app["conf"]["interfaces_default_data"][terminal]
    body = json.dumps(response_data).encode('utf-8')
    return aiohttp.web.Response(body=body, content_type="application/json") 


def http_ipc_init(db, loop, conf):
    app = aiohttp.web.Application(loop=loop)
    app['db'] = db
    app['conf'] = conf
    app.router.add_route('*', conf.ipc.path_routes_add,
                         http_ipc_handle_routes_add)
    app.router.add_route('*', conf.ipc.path_interfaces_get,
                         http_ipc_handle_interfaces_get)
    server = loop.create_server(app.make_handler(),
                                conf.ipc.v4_listen_addr,
                                conf.ipc.v4_listen_port)
    fmt = "HTTP IPC server started at http://{}:{}\n"
    msg(fmt.format(conf.ipc.v4_listen_addr, conf.ipc.v4_listen_port))
    loop.run_until_complete(server)



def db_init():
    db = addict.Dict()
    return db


def main(conf):
    db = db_init()
    loop = asyncio.get_event_loop()
    http_ipc_init(db, loop, conf)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", help="configuration", type=str, default=None)
    parser.add_argument("-v", "--verbose", help="verbose", action='store_true', default=False)
    args = parser.parse_args()
    if not args.configuration:
        err("Configuration required, please specify a valid file path, exiting now\n")
    return args


def load_configuration_file(args):
    with open(args.configuration) as json_data:
        return addict.Dict(json.load(json_data))


def init_global_behavior(args, conf):
    global DEBUG_ON
    if conf.common.debug or args.verbose:
        msg("Debug: enabled\n")
        DEBUG_ON = True
    else:
        msg("Debug: disabled\n")


def conf_init():
    args = parse_args()
    conf = load_configuration_file(args)
    init_global_behavior(args, conf)
    return conf


if __name__ == '__main__':
    msg("Terminaler, 2016\n")
    conf = conf_init()
    main(conf)
