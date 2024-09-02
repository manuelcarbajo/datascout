use warnings;
use strict;
use feature 'say';

#>sp|Q1PCB1|PDXK_BOMMO Pyridoxal kinase OS=Bombyx mori OX=7091 GN=Pdxk PE=1 SV=1

open(IN,$ARGV[0]);
while(<IN>) {
  my $line = $_;

  if($line =~ /\>[^\|]+\|([^\|]+)\|.+SV\=(\d+)/) {
    my $header = ">".$1.".".$2;
    say $header;
  } else {
    print($line);
  }
}
close IN;

exit;

