def djb2(string):
   hashCode = 5381
   for i in string:
      hashCode = ((hashCode << 5) + hashCode) + ord(i)
   return hashCode


def fnv32a(str):
   hashCode = 0x811c9dc5
   fnv_32_prime = 0x01000193
   uint32_max = 2**32
   for s in str:
      hashCode ^= ord(s)
      hashCode *= fnv_32_prime
   return hashCode & (uint32_max - 1)
