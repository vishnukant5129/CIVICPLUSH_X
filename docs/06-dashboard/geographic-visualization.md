# Geographic Visualization

We utilize **React Leaflet** integrated with an open-source OSM tile layer to render authentic geospatial map plots of complaint coordinates.

## Constraints
- **Zero Fake Data:** A map marker is only rendered if an actual database coordinate vector exists within the GeoJSON shape inside the complaint document. If the frontend retrieves a `FeatureCollection` with zero features, the map falls back to a clean text empty state.
- **Privacy:** In Phase 6 MVP, markers expose precise stored coordinates scoped strictly to the original author. No cross-user leakage exists, so coordinate fuzzing for privacy is not yet necessary.
- **Payload Limits:** The map API caps coordinates sent to the frontend at `1000` elements to protect browser rendering loops and database egress bandwidth limits.
