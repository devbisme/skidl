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
if USING_PYTHON3:
    from PySpice import *
    from PySpice.Unit import *
    from .libs.pyspice_sklib import *

    set_net_bus_prefixes('N', 'B')  # Use prefixes with no odd characters for SPICE.

    set_default_tool(SKIDL)     # Set the library format for reading SKiDL libraries.
    _splib = SchLib('pyspice')  # Read-in the SPICE part library.

    GND = gnd = Net('0')  # Instantiate the default ground net for SPICE.
