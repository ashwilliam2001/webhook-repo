import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WebhookService {
  private apiUrl = 'http://localhost:5000/requests';

  constructor(private http: HttpClient) { }

  getRequests(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }
}
