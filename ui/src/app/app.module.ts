import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import { NgModule } from '@angular/core';

import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { SitemapComponent } from './sitemap/sitemap.component';

import { NgxGraphModule } from '@swimlane/ngx-graph';
import { CommitsComponent } from './commits/commits.component';
import { ProjectsComponent } from './projects/projects.component';
import { DataService } from './data.service';
import { PageComponent } from './page/page.component';
import { DiffComponent } from './diff/diff.component';
import { TabsComponent } from './tabs/tabs.component';
import { TabComponent } from './tabs/tab.component';

@NgModule({
  declarations: [
    AppComponent,
    SitemapComponent,
    CommitsComponent,
    ProjectsComponent,
    PageComponent,
    DiffComponent,
    TabsComponent,
    TabComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    NgxGraphModule
  ],
  providers: [DataService],
  bootstrap: [AppComponent]
})
export class AppModule { }
