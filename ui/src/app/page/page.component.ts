import { Component, OnInit, Input, SimpleChanges, OnChanges, EventEmitter, Output } from '@angular/core';
import { DataService } from '../data.service';
import { tidy_html5 } from '../../assets/tidy';
import { map } from 'rxjs-compat/operator/map';


@Component({
  selector: 'app-page',
  templateUrl: './page.component.html',
  styleUrls: ['./page.component.css']
})
export class PageComponent implements OnInit, OnChanges {

  @Input() page;

  @Output() closePage = new EventEmitter();

  public Object = Object;

  public diffs = [];
  public pageDiffs = {};
  public actionDiffs = {};
  public formDiffs = {};

  public pageCount = 0;
  public actionCount = 0;
  public formCount = 0;

  constructor(private service: DataService) { }

  ngOnInit () {

  }

  ngOnChanges (changes: SimpleChanges) {
    if (this.page != null)
      this.getDiffs(this.page.id);
    else
      this.diffs = [];
  }

  getDiffs (id) {
    const options = {
      "indent": "auto",
      "indent-spaces": 2,
      "wrap": 80,
      "markup": true,
      "output-xml": false,
      "numeric-entities": true,
      "quote-marks": true,
      "quote-nbsp": false,
      "show-body-only": true,
      "quote-ampersand": false,
      "break-before-br": true,
      "uppercase-tags": false,
      "uppercase-attributes": false,
      "drop-font-tags": true,
      "tidy-mark": false
    }

    this.service.getDiffs(id).subscribe((data: any[]) => {
      this.diffs = data;

      let pages = this.diffs.filter(x => x.action == null);
      let actions = this.diffs.filter(x => x.action != null && x.action != "form");
      let forms = this.diffs.filter(x => x.action != null && x.action == "form");

      this.pageCount = pages.length;
      this.actionCount = actions.length;
      this.formCount = forms.length;

      this.pageDiffs = this.mergeDiffs(pages);
      this.actionDiffs = this.mergeDiffs(actions);
      this.formDiffs = this.mergeDiffs(forms);

    });
  }

  mergeDiffs (diffs) {
    let destination = {};

    for (const diff of diffs) {
      if (destination[diff.element] == null) {
        destination[diff.element] = []
      }

      destination[diff.element].push(diff)
    }

    return destination;
  }

  close () {
    this.closePage.emit(true);
  }
}
