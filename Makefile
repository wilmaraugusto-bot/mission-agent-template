.PHONY: run docker-up clean

run:
	python -m agent.main

docker-up:
	docker compose up --build

clean:
	rm -rf runs/*
	touch runs/.gitkeep
