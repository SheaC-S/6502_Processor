# utils.py
import functools
import traceback


def safe_execution(func):
    """
    A decorator that wraps IDE methods in a unified error handler
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self)

        except StopIteration:
            # Graceful Halt (BRK instruction)
            self.is_running = False
            self.timer.stop()
            self.run_button.setText("Run")
            self.editor.clear_active_line()
            self.log_to_console("Program finished (Hit BRK / $00).")

        except Exception as e:
            # Crash / Error Handler
            self.is_running = False
            self.timer.stop()
            self.run_button.setText("Run")

            self.log_to_console(f"ERROR: {str(e)}")

    return wrapper