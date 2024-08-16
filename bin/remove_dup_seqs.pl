use warnings;
use strict;
use feature 'say';


my $seq_hash = {};

my @all_lines = ();
my $count = 0;
open(IN,$ARGV[0]);
while(<IN>) {
  my $line = $_;
  chomp($line);
  if($line =~ /\>/) {
    if($count) {
      $count++;
      $all_lines[$count] = $line;
      $count++;
    } else {
      $all_lines[$count] = $line;
      $count++;
    }
  } else {
    if($all_lines[$count]) {
      $all_lines[$count] .= $line;
    } else {
      $all_lines[$count] = $line;
    }
  }

}
close IN;

for(my $i=0; $i<scalar(@all_lines); $i+= 2) {
  my $header = $all_lines[$i];
  my $seq = $all_lines[$i+1];
  unless(length($seq) >= 100) {
    next;
  }
  $seq_hash->{$seq} = $header;
}

foreach my $key (keys(%{$seq_hash})) {
  say $seq_hash->{$key};
  say $key;
}

exit;

