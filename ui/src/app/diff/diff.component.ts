import { Component, OnInit, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-diff',
  templateUrl: './diff.component.html',
  styleUrls: ['./diff.component.css']
})
export class DiffComponent implements OnInit, OnChanges {

  @Input() data;

  constructor() { }

  ngOnInit () {
  }

  ngOnChanges (changes: SimpleChanges) {
    console.log(this.data);
  }

}
