def run(payload: dict):
    # adapter: payload může obsahovat path nebo config; volá pipeline krok po kroku
    from vinyl_preflight.core.pipeline import ingest, extract, validate, report
    p = ingest(payload.get('source', 'in-memory'))
    r = extract(p)
    r2 = validate(r)
    rep = report(r2)
    return {'status': 'done', 'report': rep}

