#__main__.py
import argparse
import sys
import os
import config
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
found_parent_dir = False
for p in sys.path:
    if os.path.abspath(p) == PARENT_DIR:
        found_parent_dir = True
        break
if not found_parent_dir:
    sys.path.insert(0, PARENT_DIR)

def main():
    parser = argparse.ArgumentParser(description='Job Scheduler Service')
    parser.add_argument(
        '-t', '--topology',
        default='config/topology_local.json',
        help='Loads topology from the given path'
    )
    parser.add_argument(
        '-c', '--config',
        default='config_controller.json',
        help='Loads configuration from the given path.'
    )
    parser.add_argument(
        '-d', '--debug',
        action="store_true",
        help='Runs the application in Debug mode'
    )
    args = parser.parse_args()
    import config
    try:
        config.init(args.topology, args.config, args.debug)
    except:
        raise

    from log import logger
    if args.debug:
        logger.info("Program runs in debug mode")
    
    import service_manager
    try:
        service_manager.start()
        service_manager.app.run(debug=args.debug, host="0.0.0.0", port=config.general.port)
    except Exception as err:
        logger.error("Can't run the service due to: %s", err.message)
        print 'err'
    finally:
        service_manager.stop()

if __name__ == '__main__':
    main()

