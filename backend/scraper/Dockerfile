FROM smarkets-base-image
WORKDIR /app
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "backend.scraper.src.main:app", "--host", "0.0.0.0", "--port", "8001"]
