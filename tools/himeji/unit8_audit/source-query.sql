select s.game,s.side,s.team,s.map,s.round,s.ended,g.ranked,g.series_id,
          cast(g.started_at as varchar) started_at,
          coalesce(s.c_eats_bed,0) bed_eats,coalesce(s.c_splits,0) splits,
          coalesce(s.c_transits,0) transits,s.territory,s.units,s.total,
          coalesce(s.c_eats_bed,0)/nullif(s.c_bed_spawns,0) bed_capture
          from read_parquet(?,union_by_name=true,filename=true) s
          join canon k on k.game=s.game and replace(s.filename,'/series/','/sides/')=k.part
          join g on g.game=s.game where s.round in (25,50)
