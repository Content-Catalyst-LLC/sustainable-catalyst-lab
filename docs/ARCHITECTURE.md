# Lab v0.2.0 Architecture

WordPress renders the scientific interface and proxies public source APIs through REST routes. Browser modules normalize feed records into observations and datasets, preserve provenance, and store project records locally. The Dataset Inspector is source-agnostic and can inspect normalized feed records, imported JSON, or CSV. Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes.
