#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Import this file to reconfigure SKiDL for doing SPICE simulations.
"""

from skidl import *

# PySpice only works with Python 3, so don't set up SPICE simulation for Python 2.
try:
    from PySpice import *
    from PySpice.Unit import *
    from .libs.pyspice_sklib import *
    from .tools.spice import *
except ImportError:
    pass
else:
    _splib = SchLib('pyspice', tool=SKIDL)  # Read-in the SPICE part library.

    set_default_tool(SPICE)     # Set the library format for reading SKiDL libraries.

    set_net_bus_prefixes('N', 'B')  # Use prefixes with no odd characters for SPICE.

    GND = gnd = Net('0')  # Instantiate the default ground net for SPICE.
    gnd.fixed_name = True # Make sure ground keeps it's name of "0" during net merges.

    # Place all the PySpice parts into the namespace so they can be instantiated easily.
    _this_module = sys.modules[__name__]
    for p in _splib.get_parts():
        # Add the part name to the module namespace.
        setattr(_this_module, p.name, p)
        # Add all the part aliases to the module namespace.
        try:
            for alias in p.aliases:
                setattr(_this_module, alias, p)
        except AttributeError:
            pass
