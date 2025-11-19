# Copyright 1999-2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DISTUTILS_USE_PEP517=setuptools
PYTHON_COMPAT=( python3_{10..13} )

inherit distutils-r1 git-r3

DESCRIPTION="SKiDL is a module that allows you to compactly describe the interconnection of electronic circuits and components using Python"
HOMEPAGE="https://devbisme.github.io/${PN} https://github.com/devbisme/${PN} https://pypi.org/project/${PN}"

EGIT_REPO_URI="https://github.com/devbisme/${PN}.git"

LICENSE="MIT"
SLOT="0"
IUSE="spice"

RDEPEND="
	>=dev-python/sexpdata-1.0.0[${PYTHON_USEDEP}]
	>=dev-python/kinparse-1.2.1[${PYTHON_USEDEP}]
	>=dev-python/kinet2pcb-1.1.0[${PYTHON_USEDEP}]
	dev-python/graphviz[${PYTHON_USEDEP}]
	dev-python/deprecation[${PYTHON_USEDEP}]
	spice? ( >=dev-python/PySpice-1.3.2[${PYTHON_USEDEP}] )
"

distutils_enable_tests pytest

S=${WORKDIR}/${P}