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
	SRC_URI="https://files.pythonhosted.org/packages/19/01/1d98cd0e18ab5485850f1b30c28ad4e8a768dfe43a2852c2efaf6c369775/${P}.tar.gz"
	KEYWORDS="~amd64 ~x86"
fi

DESCRIPTION="This PCBNEW plugin arranges the parts into groups that reflect the hierarchy in the design"
HOMEPAGE="https://devbisme.github.io/${PN} https://github.com/devbisme/${PN} https://pypi.org/project/${PN}"

LICENSE="MIT"
SLOT="0"

distutils_enable_tests pytest

S=${WORKDIR}/${P}
