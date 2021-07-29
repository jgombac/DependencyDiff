import { Component } from '@angular/core';
import { DataService } from './data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [DataService]
})
export class AppComponent {
  title = 'ui';

  public projects = [];
  public pages = [];
  public links = [];

  constructor(private service: DataService) {

  }

  ngOnInit () {
    this.getProjects();
  }

  private getProjects () {
    this.service.getProjects().subscribe((data: any[]) => this.projects = data)
  }

  public pagesLoaded (data) {
    this.pages = data.pages;
    this.links = data.links;
  }
}
