#! /usr/bin/perl
use strict;
use warnings;

use PDL;
use PDL::Graphics::PGPLOT;
use Chandra::Tools::Common qw/ read_bintbl_cols /;

my $f1 = './srcflux/i_qe_N0011/24982_plerion_0001.arf';
my $f2 = './srcflux/i_qe_N0013/24982_plerion_0001.arf';

my ($e1, $arf1) = read_bintbl_cols($f1.'[1]', qw/ energ_lo specresp / );
my ($e2, $arf2) = read_bintbl_cols($f2.'[1]', qw/ energ_lo specresp / );

dev '/xs', 1, 3;

line $e1, $arf1, { border => 0.1 };
line $e2, $arf2, { border => 0.1 };
line $e1, $arf1/$arf2, { yrange => [0.8, 1.2], border => 0.1 };

print( join("\t", ($arf1-$arf2)->minmax), "\n" );
