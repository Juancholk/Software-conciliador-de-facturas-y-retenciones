import { Service, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { EstadoFactura, ResultadoConciliacion } from '../models/resultado.model';

@Service()
export class Conciliacion {
  private http = inject(HttpClient);
  private api = 'http://localhost:8000/api';

  /** Envía los dos archivos y devuelve el resultado completo. */
  conciliar(facturas: File, contabilidad: File) {
    const form = new FormData();
    form.append('facturas', facturas);         // mismo nombre que en FastAPI
    form.append('contabilidad', contabilidad);
    return this.http.post<ResultadoConciliacion>(`${this.api}/conciliar`, form);
  }

  /** Consulta el último resultado procesado, opcionalmente filtrado por estado. */
  consultar(estado?: EstadoFactura) {
    let params = new HttpParams();
    if (estado) {
      params = params.set('estado', estado);
    }
    return this.http.get<ResultadoConciliacion>(`${this.api}/resultados`, { params });
  }
}
