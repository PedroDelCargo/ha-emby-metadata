"""Pure helpers shared by the sensor, coordinator and image entities."""

ITEM_FIELDS = frozenset("Id Name Type OriginalTitle Tagline Taglines ProductionYear PremiereDate Overview Genres OfficialRating CommunityRating CriticRating RunTimeTicks Container Bitrate MediaStreams MediaSources ProviderIds ImageTags BackdropImageTags ParentBackdropItemId ParentBackdropImageTags ParentLogoItemId ParentLogoImageTag SeriesId SeriesName SeasonId SeasonName ParentIndexNumber IndexNumber IndexNumberEnd SeriesPrimaryImageTag People".split())


def people(item):
    """Keep named people in a stable order, with identical slots in all entities."""
    result, seen = [], set()
    for person in item.get("People") or []:
        if not isinstance(person, dict) or not person.get("Name"):
            continue
        kind = str(person.get("Type") or "").lower()
        if kind in {"gueststar", "guest star"}:
            kind = "actor"
        key = (kind, str(person.get("Id") or person["Name"]))
        if kind not in {"actor", "director"} or key in seen:
            continue
        seen.add(key)
        result.append({k: person.get(k) for k in ("Id", "Name", "Role", "PrimaryImageTag")} | {"Type": kind})
    return result


def normalize_item(current, details=None, series=None, season=None, media_source_id=None):
    """Enrich the current item without copying volatile playback/user data."""
    item = dict(current)
    item.update({k: v for k, v in (details or {}).items() if v is not None})
    # The session's streams describe the version actually being played.
    if current.get("MediaStreams"):
        item["MediaStreams"] = current["MediaStreams"]
    sources = item.get("MediaSources") or []
    source = next((s for s in sources if str(s.get("Id")) == str(media_source_id)), None)
    if source is None and len(sources) == 1:
        source = sources[0]
    if source and source.get("MediaStreams") and (media_source_id or not item.get("MediaStreams")):
        item["MediaStreams"] = source["MediaStreams"]
    item = {k: v for k, v in item.items() if k in ITEM_FIELDS and k != "MediaSources"}
    series, season = series or {}, season or {}
    if item.get("Type") in {"Episode", "Season"}:
        item["SeriesName"] = item.get("SeriesName") or series.get("Name")
        for field in ("Overview", "Genres", "OfficialRating"):
            item[field] = item.get(field) or season.get(field) or series.get(field)
    # Episode director wins; series cast supplements incomplete episode credits.
    merged = people(item)
    for parent in (season, series):
        merged = people({"People": merged + people(parent)})
    item["People"] = merged
    item["Tagline"] = item.get("Tagline") or next(iter(item.get("Taglines") or []), None)
    item["_images"] = image_sources(item, series, season)
    return item


def image_sources(item, series=None, season=None):
    series, season = series or {}, season or {}

    def own(obj, kind):
        tags = obj.get("ImageTags") or {}
        tag = next(iter(obj.get("BackdropImageTags") or []), None) if kind == "Backdrop" else tags.get(kind)
        return (str(obj["Id"]), kind, tag) if obj.get("Id") and tag else None

    def inherited(id_key, tag_key, kind, multiple=False):
        tag = item.get(tag_key)
        if multiple:
            tag = next(iter(tag or []), None)
        return (str(item[id_key]), kind, tag) if item.get(id_key) and tag else None

    poster = own(item, "Primary")
    if item.get("Type") == "Episode":
        poster = (own(season, "Primary") or own(series, "Primary")
                  or inherited("SeriesId", "SeriesPrimaryImageTag", "Primary") or poster)
    return {
        "poster": poster,
        "backdrop": own(item, "Backdrop") or inherited("ParentBackdropItemId", "ParentBackdropImageTags", "Backdrop", True) or own(series, "Backdrop") or own(season, "Backdrop") or (own(item, "Primary") if item.get("Type") == "Episode" else None),
        "logo": own(item, "Logo") or inherited("ParentLogoItemId", "ParentLogoImageTag", "Logo") or own(series, "Logo") or own(season, "Logo"),
    }


def image_source(item, kind):
    if not item:
        return None
    if kind in {"poster", "backdrop", "logo"}:
        return (item.get("_images") or image_sources(item)).get(kind)
    entries = people(item)
    if kind == "director":
        selected = next((p for p in entries if p["Type"] == "director"), None)
    elif kind.startswith("actor_") and kind[6:].isdigit():
        actors = [p for p in entries if p["Type"] == "actor"][:5]
        index = int(kind[6:]) - 1
        selected = actors[index] if 0 <= index < len(actors) else None
    else:
        selected = None
    # An ID can serve a Primary image even when Emby omits its tag.
    return (str(selected["Id"]), "Primary", selected.get("PrimaryImageTag")) if selected and selected.get("Id") else None


def hdr_value(video):
    for key in ("ExtendedVideoType", "VideoRange"):
        value = video.get(key)
        if value and str(value).strip().lower() not in {"none", "null", "sdr", "0", "unknown"}:
            return value
    return None
