import { Component, OnInit, Input, Output } from '@angular/core';
import { DataService } from '../data.service';
import { EventEmitter } from '@angular/core';

@Component({
  selector: 'app-projects',
  templateUrl: './projects.component.html',
  styleUrls: ['./projects.component.css']
})
export class ProjectsComponent implements OnInit {
  @Input() projects;
  @Output() pagesLoaded = new EventEmitter();

  private selected;
  public commits = [];

  constructor(private service: DataService) { }

  ngOnInit () {
  }

  public isSelected (project) {
    return this.selected && project.id == this.selected.id;
  }

  public select (project) {
    if (this.isSelected(project))
      return;

    this.selected = project;
    this.commits = [];
    this.getCommits(project.id);
  }

  public getCommits (id) {
    this.service.getCommits(id).subscribe((data: any[]) => this.commits = data)
  }

  public getPages (id) {
    this.service.getPages(id).subscribe((data: any[]) => this.pagesLoaded.emit(data))
  }
}
