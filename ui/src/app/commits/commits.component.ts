import { Component, OnInit, Input, Output } from '@angular/core';
import { EventEmitter } from '@angular/core';


@Component({
  selector: 'app-commits',
  templateUrl: './commits.component.html',
  styleUrls: ['./commits.component.css']
})
export class CommitsComponent implements OnInit {

  private selected;

  @Input() commits = [];

  @Output() commitSelected = new EventEmitter();

  constructor() { }

  ngOnInit () {

  }

  public setData () {
  }

  public isSelected (commit) {
    return this.selected && commit.id == this.selected.id;
  }

  public select (commit) {
    if (this.isSelected(commit))
      return;

    this.selected = commit;
    this.commitSelected.emit(commit.id);
  }

}
