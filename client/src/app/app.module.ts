// Modules
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CookieModule } from 'ngx-cookie';
import { CookieService } from 'ngx-cookie';
import { StoreModule } from '@ngrx/store';
import { routerReducer, RouterStoreModule } from '@ngrx/router-store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { StoreLogMonitorModule, useLogMonitor } from '@ngrx/store-log-monitor';

// Application
import { AppComponent } from './app.component';
import { AppMaterial } from './app.material';
import { routing } from './app.routing';
import { AuthGuard } from './guards/auth.guard';
import { SafeStylePipe } from './pipes/safe-style.pipe';

// Services
import { AuthService } from './services/auth.service';
import { FlickrService } from './services/flickr.service';
import { ImageService } from './services/image.service';

// Actions
import { AuthActions } from './actions/auth.actions';
import { SearchActions } from './actions/search.actions';
import { AnnotateActions } from './actions/annotate.actions';
import { CardLayoutActions } from './actions/card-layout.actions';
import { ArtboardActions } from './actions/artboard.actions';

// Effects
import { AuthEffects } from './effects/auth.effects';
import { SearchEffects } from './effects/search.effects';
import { AnnotateEffects } from './effects/annotate.effects';

// Reducers
import { authReducer } from './reducers/auth.reducer';
import { searchReducer } from './reducers/search.reducer';
import { annotateReducer } from './reducers/annotate.reducer';
import { cardLayoutReducer } from './reducers/card-layout.reducer';
import { artboardReducer } from './reducers/artboard.reducer';
import { objectXReducer } from './reducers/object-x.reducer';
import { nudityCheckReducer } from './reducers/nudity-check.reducer';

// Components
import { LoginComponent } from './components/+login/login.component';
import { SearchComponent } from './components/+search/search.component';
import { AnnotateComponent } from './components/+annotate/annotate.component';
import { SkinPixelsComponent } from './components/+skin-pixels/skin-pixels.component';
import { NudityCheckComponent } from './components/+nudity-check/nudity-check.component';
import { ObjectXComponent } from './components/+object-x/object-x.component';
import { AttributesComponent } from './components/+attributes/attributes.component';

import { CardListComponent } from './components/card-list/card-list.component';
import { CardComponent } from './components/card/card.component';
import { AnnotateStepsComponent } from './components/annotate-steps/annotate-steps.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';


export function instrumentOptions() {
  return {
    monitor: useLogMonitor({ visible: true, position: 'right' })
  };
}

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    SearchComponent,
    SafeStylePipe,
    CardComponent,
    SkinPixelsComponent,
    PageNotFoundComponent,
    NudityCheckComponent,
    ObjectXComponent,
    AttributesComponent,
    AnnotateStepsComponent,
    AnnotateComponent,
    CardListComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpModule,
    routing,
    BrowserAnimationsModule,
    CookieModule.forRoot(),
    AppMaterial,
    StoreModule.provideStore({
      auth: authReducer,
      search: searchReducer,
      annotate: annotateReducer,
      cardLayout: cardLayoutReducer,
      router: routerReducer,
      artboard: artboardReducer,
      objectX: objectXReducer,
      nudityCheck: nudityCheckReducer,
    }),
    RouterStoreModule.connectRouter(),
    EffectsModule.runAfterBootstrap(AuthEffects),
    EffectsModule.runAfterBootstrap(SearchEffects),
    EffectsModule.runAfterBootstrap(AnnotateEffects),
    StoreDevtoolsModule.instrumentStore(instrumentOptions),
    StoreLogMonitorModule,
  ],
  providers: [
    AuthGuard,
    AuthService,
    CookieService,
    FlickrService,
    ImageService,
    AuthActions,
    SearchActions,
    AnnotateActions,
    CardLayoutActions,
    ArtboardActions,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
