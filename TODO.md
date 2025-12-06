# TODO: Adapt app.py for Mental Health Models

- [x] Update imports to include Disorder and Assessment instead of Genre and Catalogue
- [x] Change GenreSchema to DisorderSchema with name, description, symptoms
- [x] Change CatalogueSchema to AssessmentSchema with session_id, answers (str), result, severity_score, disorder_id (int)
- [x] Update route paths: /genre -> /disorder, /catalogue -> /assessment
- [x] Implement get_single_disorder method
- [x] Implement update_disorder method
- [x] Implement delete_disorder method
- [x] Implement get_single_assessment method
- [x] Implement update_assessment method
- [x] Implement delete_assessment method
- [x] Ensure all routes follow the provided format structure
- [x] Test the API endpoints after changes
