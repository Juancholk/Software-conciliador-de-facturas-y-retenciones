export type EstadoFactura = 'Correcta' | 'Con inconsistencia';

export interface Causa {
  codigo: string;
  descripcion: string;
  detalle: string;
}

export interface Calculos {
  iva_esperado: number | null;
  iva_reportado: number | null;
  retencion_esperada: number | null;
  retencion_reportada: number | null;
  total_esperado: number | null;
  total_reportado: number | null;
}

export interface FacturaResultado {
  fila: number;
  id_factura: string;
  nit_proveedor: string;
  fecha_factura: string;
  concepto: string;
  base_gravable: number | null;
  estado: EstadoFactura;
  causas: Causa[];
  calculos: Calculos;
  contabilidad: { registros: number; valor_contabilizado: number | null };
}

export interface RegistroSinFactura {
  fila: number;
  id_factura: string;
  fecha_contabilizacion: string;
  cuenta_contable: string;
  valor_debito: number | null;
  causa: Causa;
}

export interface Advertencia {
  codigo: string;
  descripcion: string;
  detalle: string;
}

export interface Resumen {
  registros_leidos: number;
  facturas_unicas: number;
  correctas: number;
  con_inconsistencia: number;
  por_causa: Record<string, number>;
  monto_diferencias: {
    iva: number;
    retencion: number;
    total: number;
    valor_contable: number;
  };
  registros_contables_leidos: number;
  registros_contables_sin_factura: number;
}

export interface ResultadoConciliacion {
  resumen: Resumen;
  detalle: FacturaResultado[];
  registros_sin_factura: RegistroSinFactura[];
  advertencias: Advertencia[];
}
