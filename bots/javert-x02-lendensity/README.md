# Javert x02: length-density information (D2/R2)

On top of x01: the density estimator additionally tracks EWMA sums of
visible ally/enemy segments (own length included) and sends them in a new
type-7 sonar packet beside the type-6 counts on a second reserved ray
(crown/prey rays still protected). Receivers merge type-6/type-7 rows by
(sender mod 512, round) with matching rounded position; field_len() exposes a
decayed length field. Nothing consumes it in this cell: this isolates the
information/communication change from its policy use.
All javert-x0* cells share identical executable files except `settings.py`.
See the Javert report (`../../docs/javert.md`) for the controlled study.
