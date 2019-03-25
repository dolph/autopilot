import argparse
import os
import pdb

from autopilot import browser
from autopilot import robinhood


def cli():
    parser = argparse.ArgumentParser(description='Browse on autopilot.')
    parser.add_argument(
        '--fullscreen',
        help='Run browser in fullscreen mode.',
        action='store_true',
        default=os.getenv('BROWSER_FULLSCREEN') == 'true')
    parser.add_argument(
        '--headless',
        help='Run browser in headless mode.',
        action='store_true',
        default=os.getenv('BROWSER_HEADLESS') == 'true')
    parser.add_argument(
        '--debug',
        help='Stop to debug in the event of an exception.',
        action='store_true',
        default=os.getenv('BROWSER_DEBUG') == 'true')

    # Add subparsers for individual commands
    subparsers = parser.add_subparsers()
    robinhood.add_subparser(subparsers)

    args = parser.parse_args()

    # Validate arguments
    if args.fullscreen and args.headless:
        raise Exception(
            'Cannot specify BROWSER_HEADLESS and BROWSER_FULLSCREEN '
            'options at the same time.')

    b = None
    error = False
    try:
        b = browser.Browser(
            fullscreen=args.fullscreen,
            headless=args.headless)
        c = args.func(b, args)
        c.start()
    except Exception:
        error = True
        if args.debug:
            pdb.set_trace()
        raise
    finally:
        if b:
            if not error and args.debug:
                pdb.set_trace()
            b.quit()
