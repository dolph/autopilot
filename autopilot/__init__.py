import argparse
import imp
import os
import pdb

from autopilot import browser


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
    parser.add_argument(
        '--verbose',
        help='Verbose logging of state to stdout.',
        action='store_true',
        default=os.getenv('BROWSER_VERBOSE') == 'true')
    parser.add_argument(
        'module',
        help='Path to the autopilot module where `start(browser)` should be '
             'called.')

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
            headless=args.headless,
            verbose=args.verbose)
        autopilot_module = imp.load_source('autopilot_module', args.module)
        autopilot_module.start(b)
    except SystemExit:
        error = False
        raise
    except Exception as e:
        error = True
        if args.debug:
            if args.verbose:
                print(e)
            pdb.set_trace()
        raise
    finally:
        if b:
            if not error and args.debug:
                pdb.set_trace()
            b.quit()
