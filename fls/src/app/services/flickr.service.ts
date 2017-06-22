import { Injectable } from '@angular/core';
import { Http, Headers, RequestOptions, Response } from '@angular/http';
import { PlatformLocation } from '@angular/common';
import { CookieService } from 'ngx-cookie';
import { FlickrSearch, FlickrImage, License } from '../models/flickr.models';
import { map, filter, union } from 'underscore';
import { Observable } from 'rxjs/Observable';
import { environment } from '../../environments/environment';

import 'rxjs/add/operator/mergeMap';

@Injectable()
export class FlickrService {

  private endpoint: string;
  private apiKey: string;

  constructor(
    private http: Http,
    private cookieService: CookieService) {
    this.endpoint = environment.apiURL;
  }

  getSearch(id: number) {
    console.log(id);
  }

  getLicenses(): Observable<License[]> {
    return this.http.get(`${this.endpoint}licenses/`, this.jwt())
      .map((response: Response) => response.json())
      .map(result => result.map(data => new License(data)));
  }

  getSavedImages(): Observable<FlickrImage[]> {
    return this.http.get(`${this.endpoint}images/`, this.jwt())
      .map((response: Response) => response.json())
      .map(data => data.map(image => new FlickrImage(image)));
  }

  search(search: FlickrSearch, licenses: License[], page: number): Observable<any> {

    let queryStr = search.query;
    let excludeStr = search.exclude.split(',').map(str => ` -${str.trim()}`).join(',');
    var searchQuery = queryStr;
    if (excludeStr != '-') {
      searchQuery += `,${excludeStr}`;
    }

    let url = `${this.endpoint}search/` +
      `&license=${licenses.map(license => license.id).sort().join(',')}` +
      `&user_id=${search.userID}` +
      `&per_page=${search.perPage}` +
      `&page=${page}` +
      `&tags=${searchQuery}` +
      `&tag_mode=${search.tagMode.value}`;

    return this.http.get(url, this.jwt())
      .map((response: Response) => response.json());
      // .map((result: any) => {
      //   return {
      //     totalPages: result.total,
      //     results: result.results.map(photo => new FlickrImage(photo))
      //   };
      // });
  };


  saveSearch(search: FlickrSearch, images: FlickrImage[]) {
    let body = JSON.stringify({
      query: search.query,
      exclude: search.exclude || '',
      user_id: search.userID,
      tag_mode: search.tagMode.value,
      images
    });
    let currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (currentUser && currentUser.token) {
      let headers = new Headers({
        'Content-Type': 'application/json; charset=utf-8',
        'X-CSRFToken': this.cookieService.get('csrftoken'),
        'Authorization': `Token ${currentUser.token}`
      });
      let options = new RequestOptions({ headers: headers });
      return this.http.post(`${this.endpoint}search/`, body, options)
        .map((response: Response) => response.json());
    }
  }

  private jwt() {
    // create authorization header with jwt token
    let currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (currentUser && currentUser.token) {
      let headers = new Headers({
        'Authorization': `Token ${currentUser.token}`
      });
      return new RequestOptions({ headers: headers });
    }
  }

}
