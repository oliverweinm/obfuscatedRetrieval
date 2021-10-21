from .connection import Function

class obfuscatedRetrievalFunction(Function):
	"""Conection to the obfuscatedRetrieval app to insert and output the request and response events"""

	def __init__(self):
		super(obfuscatedRetrievalFunction, self).__init__()

	def insert_obfuscatedRetrieval_event(self, cbor):
		"""Inserts a new chat element as cbor"""
		self.insert_event(cbor)

	#TODO
	def get_all_events_since(self, timestamp, feed_id):
		pass

	#TODO
	def get_all_events(self, timestamp, feed_id):
		raise NotImplementedError

	#TODO
	def _get_all_response_events_since(self, timestamp, feed_id):
		raise NotImplementedError

	#TODO
	def get_all_response_events_since(self, timestamp, feed_id):
		raise NotImplementedError