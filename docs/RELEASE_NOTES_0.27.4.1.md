# Sustainable Catalyst Lab v0.27.4.1

## WordPress Integrity Manifest Scope Repair

The v0.27.4 source manifest included WordPress and Python backend files in one `criticalFiles` map. The WordPress deployment ZIP intentionally excludes `backend/`, so the runtime integrity checker incorrectly classified valid installations as partial or mismatched.

v0.27.4.1 separates the manifest into WordPress and backend scopes. The WordPress runtime verifies only files present in the plugin package, while backend hashes remain available for source and backend package validation.

No scientific method, visualization, queue, or Render backend behavior changes in this patch.
