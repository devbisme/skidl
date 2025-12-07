# Copyright 1999-2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DISTUTILS_USE_PEP517=setuptools
PYTHON_COMPAT=( python3_{10..13} )

inherit distutils-r1

if [[ ${PV} == 9999 ]]; then
	inherit git-r3
	EGIT_REPO_URI="https://github.com/devbisme/${PN}.git"
else
	SRC_URI="https://github.com/devbisme/${PN}/archive/refs/tags/${PV}.tar.gz -> ${P}.gh.tar.gz"
	KEYWORDS="~amd64 ~x86"
fi

DESCRIPTION="This is a parser for KiCad schematic netlist files that are output by EESCHEMA"
HOMEPAGE="https://devbisme.github.io/${PN} https://github.com/devbisme/${PN} https://pypi.org/project/${PN}"

LICENSE="MIT"
SLOT="0"

RDEPEND="
	>=dev-python/pyparsing-2.1.1[${PYTHON_USEDEP}]
"

distutils_enable_tests pytest

S=${WORKDIR}/${P}