import { Component, OnInit, Input, SimpleChanges, OnChanges } from '@angular/core';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-sitemap',
  templateUrl: './sitemap.component.html',
  styleUrls: ['./sitemap.component.css']
})
export class SitemapComponent implements OnInit, OnChanges {
  @Input() pages = [];
  @Input() links = [];

  center$ = new Subject();
  zoomToFit$ = new Subject();

  public displayLinks = [];
  public displayPages = [];

  private showLinks = false;

  public selectedPage = null;

  public diffsOnly = false;

  constructor() { }

  ngOnInit () {

  }

  public selectNode (node) {
    if (node.disabled) {
      return;
    }
    console.log(node);
    this.selectedPage = node;
  }

  ngOnChanges (changes: SimpleChanges) {
    this.refreshPagesDisplay();
    this.selectedPage = null;
  }

  public toggleLinks () {
    this.showLinks = !this.showLinks;
    this.refreshPagesDisplay();
  }

  private refreshPagesDisplay () {
    const _pages = this.pages ? this.pages : [];
    if (!this.diffsOnly)
      this.displayPages = _pages.filter(x => x.diffs > 0)
    else
      this.displayPages = _pages;


    let _links = this.links ? this.links : [];
    _links = this.showLinks ? _links : [];
    this.displayLinks = _links.filter(x => this.displayPages.some(y => y.id == x.source || y.id == x.target))

    setTimeout(() => {
      this.center$.next(true);
      this.zoomToFit$.next(true);
    })
  }

  public toggleDiffsOnly () {
    this.diffsOnly = !this.diffsOnly;

    this.refreshPagesDisplay();
  }

  public closePage (close) {
    this.selectedPage = null;
  }
}
