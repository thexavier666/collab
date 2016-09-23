server:
	python collab.py
client:
	python collab.py $(ip)
clean:
	@ - rm -rf collab_downloaded_*
	@ - rm -rf collab_hosted_*
	@ - rm -rf log_*⏎
