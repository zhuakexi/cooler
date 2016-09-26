# -*- coding: utf-8 -*-
from functools import partial
import os.path as op
import tempfile
import filecmp
import os

import numpy as np
import h5py

import nose
from nose.tools import with_setup
from click.testing import CliRunner

from cooler.cli.cload import cload
from cooler.cli.csort import csort


testdir = op.realpath(op.join(op.dirname(__file__), op.pardir))
tmp = tempfile.gettempdir()
testcool_path = op.join(tmp, 'test.cool')
testcsort_path = op.join(tmp, 'test.sorted.txt.gz')
testtbi_path = op.join(tmp, 'test.sorted.txt.gz.tbi')


def teardown_func(*filepaths):
    for fp in filepaths:
        try:
            os.remove(fp)
        except OSError:
            pass


@with_setup(teardown=partial(teardown_func, testcsort_path, testtbi_path))
def test_csort():
    runner = CliRunner()
    result = runner.invoke(
        csort, [
            op.join(testdir, 'data', 'hg19-chromsizes.select.txt'),
            op.join(testdir, 'data', 'GM12878-MboI-contacts.subsample.shuffled.txt.gz'),
            '-c1', '1', '-p1', '2', '-s1', '3', '-c2', '4', '-p2', '5', '-s2', '6',
            '--out', testcsort_path,
        ]
    )
    assert result.exit_code == 0

    assert os.path.exists(testcsort_path)

    assert filecmp.cmp(
        testcsort_path,
        op.join(testdir, 'data', 'GM12878-MboI-contacts.subsample.sorted.txt.gz'))


@with_setup(teardown=partial(teardown_func, testcool_path))
def test_cload():
    runner = CliRunner()
    result = runner.invoke(
        cload, [
            op.join(testdir, 'data', 'hg19-bins.2000kb.bed.gz'),
            op.join(testdir, 'data', 'GM12878-MboI-contacts.subsample.sorted.txt.gz'),
            testcool_path
        ]
    )
    assert result.exit_code == 0

    ref_path = op.join(testdir, 'data', 'GM12878-MboI-matrix.2000kb.cool')
    with h5py.File(testcool_path, 'r') as f1, \
         h5py.File(ref_path, 'r') as f2:
        assert np.all(f1['pixels/bin1_id'][:] == f2['pixels/bin1_id'][:])
        assert np.all(f1['pixels/bin2_id'][:] == f2['pixels/bin2_id'][:])
        assert np.all(f1['pixels/count'][:] == f2['pixels/count'][:])

