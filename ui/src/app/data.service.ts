import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs-compat/operator/map';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  private url = 'http://localhost:5000/'

  constructor(private http: HttpClient) { }

  public getProjects () {
    return this.http.get(this.url + 'projects');
  }

  public getCommits (id) {
    return this.http.get(this.url + `projects/${id}`);
  }

  public getPages (id) {
    return this.http.get(this.url + `commits/${id}`)
  }

  public getDiffs (id) {
    return this.http.get(this.url + `pages/${id}`)
  }
}
