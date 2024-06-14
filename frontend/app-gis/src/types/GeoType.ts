type GeoType1 = Map<
  string | null,
  Map<
    string | null,
    Array<
      Map<
        'ctp_id' | 'buildings' | 'tecs',
        Array<Map<
          'UNOM' | 'coordinates' | 'Area',
          number | Array<Array<Array<number>>> | string
        > | null>
      >
    >
  >
>[];

type GeoType2 = Map<
  string | null,
  Array<
    Map<
      'ctp_id' | 'buildings' | 'tecs',
      Array<Map<
        'UNOM' | 'coordinates' | 'Area',
        number | Array<Array<Array<number>>> | string
      > | null>
    >
  >
>[];

type GeoType3 = Array<Map<
  'UNOM' | 'coordinates' | 'Area',
  number | Array<Array<Array<number>>> | string
> | null>;

export type { GeoType1, GeoType2, GeoType3 };
