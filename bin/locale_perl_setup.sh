# Insure the "locale" is set for unicode handling
#
for LANG in en_AU.UTF-8 en_GB.UTF-8 C.UTF-8 C; do
  if locale -a 2>/dev/null | grep -q "$LANG"; then
    export LANG
    break
  fi
done
export LC_COLLATE=C     # make 'ls' sort as 'C' order not locale order
