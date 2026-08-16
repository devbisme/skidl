# Copyright 1999-2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DISTUTILS_USE_PEP517=setuptools
PYTHON_COMPAT=( python3_{10..13} )

inherit distutils-r1

# We use patched version instead of upstream - to handle shared library NGspice correctly
SRC_URI="https://github.com/tapegoji/PySpice/archive/refs/tags/v${PV}.tar.gz -> ${P}.gh.tar.gz"
KEYWORDS="~amd64 ~x86"

DESCRIPTION="PySpice is a Python module which interfaces Python to the Ngspice and Xyce circuit simulators"
HOMEPAGE="https://pyspice.fabrice-salvaire.fr/ https://github.com/FabriceSalvaire/${PN} https://pypi.org/project/${PN}"

LICENSE="GPL-3"
SLOT="0"
IUSE="ngspice xyce"

REQUIRED_USE="|| ( ngspice xyce )"
RDEPEND="
	ngspice? ( sci-electronics/ngspice[shared] )
	xyce? ( sci-electronics/xyce )
	>=dev-python/pyyaml-5.3[${PYTHON_USEDEP}]
	>=dev-python/cffi-1.14[${PYTHON_USEDEP}]
	>=dev-python/matplotlib-3.2[${PYTHON_USEDEP}]
	>=dev-python/numpy-1.18[${PYTHON_USEDEP}]
	>=dev-python/ply-3.11[${PYTHON_USEDEP}]
	>=dev-python/scipy-1.4[${PYTHON_USEDEP}]
	>=dev-python/requests-2.23[${PYTHON_USEDEP}]
"

distutils_enable_tests pytest

S=${WORKDIR}/${P}

# TODO:
#	Subprocess mode instead of shared - then no need for shared useflag in ngspice