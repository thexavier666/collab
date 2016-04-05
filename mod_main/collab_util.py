import sys
import hashlib

class Collab_util:
	def __init__(self):
		print ""

	def mod_hash(self, given_str, search_space):
		hash_digest = hashlib.sha1()
		hash_digest.update(given_str)
		return int(hash_digest.hexdigest(),16) % search_space

def main():
	obj = Collab_util()
	print obj.mod_hash(sys.argv[1],int(sys.argv[2]))

if __name__ == '__main__':
	main()