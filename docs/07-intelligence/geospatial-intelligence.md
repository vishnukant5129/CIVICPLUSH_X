# Geospatial Intelligence & Vector Search

## MongoDB $geoNear
Because MongoDB Vector Search requires a distinct MongoDB Atlas cluster topology equipped natively with an active Search Node tier, we opted to constrain our architectural dependency matrix.

We substitute an external `$vectorSearch` with the native PyMongo `2dsphere` `$geoNear` filter.
Candidate generation prioritizes fetching surrounding documents physically via spatial indexes rather than brute-forcing $O(N^2)$ cross-world relationships.
Cosine calculation (`scipy.spatial.distance.cosine`) processes candidate matches reliably in local Python memory.
