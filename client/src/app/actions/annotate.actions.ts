import { Injectable } from '@angular/core';
import { Action } from '@ngrx/store';
import { Image, ImageState } from '../models/search.models';


@Injectable()
export class AnnotateActions {

  static REQUEST_IMAGES = '[Annotate] Request Images';
  requestImages(state: ImageState): Action {
    return {
      type: AnnotateActions.REQUEST_IMAGES,
      payload: {
        state
      }
    }
  }

  static REQUEST_IMAGES_COMPLETE = '[Annotate] Request Images Complete';
  requestImagesComplete(images: Image[], total: number): Action {
    return {
      type: AnnotateActions.REQUEST_IMAGES_COMPLETE,
      payload: {
        images,
        total
      }
    }
  }

  static SELECT_IMAGE = '[Annotate] Select Image';
  selectImage(image: Image): Action {
    return {
      type: AnnotateActions.SELECT_IMAGE,
      payload: {
        image
      }
    }
  }

  static DESELECT_IMAGE = '[Annotate] Deselect Image';
  deselectImage(): Action {
    return {
      type: AnnotateActions.DESELECT_IMAGE,
      payload: {}
    }
  }

  static REQUEST_IMAGE = '[Annotate] Request Image';
  requestImage(id: number): Action {
    return {
      type: AnnotateActions.REQUEST_IMAGE,
      payload: {
        id
      }
    }
  }

  static REQUEST_IMAGE_COMPLETE = '[Annotate] Request Image Complete';
  requestImageComplete(image: Image): Action {
    return {
      type: AnnotateActions.REQUEST_IMAGE_COMPLETE,
      payload: {
        image
      }
    }
  }

  static SELECT_STEP = '[Annotate] Select Step';
  selectStep(step: number): Action {
    return {
      type: AnnotateActions.SELECT_STEP,
      payload: {
        step
      }
    }
  }

  static UPDATE_BASE64 = '[Annotate] Update Base64';
  updateBase64(base64: string): Action {
    return {
      type: AnnotateActions.UPDATE_BASE64,
      payload: {
        base64
      }
    }
  }

  static SAVE_ANNOTATION = '[Annotate] Save Annotation';
  saveAnnotation(image: Image, base64: string): Action {
    return {
      type: AnnotateActions.SAVE_ANNOTATION,
      payload: {
        image,
        base64
      }
    }
  }

  static SAVE_ANNOTATION_COMPLETE = '[Annotate] Save Annotation Complete';
  saveAnnotationComplete(annotation: any): Action {
    return {
      type: AnnotateActions.SAVE_ANNOTATION_COMPLETE,
      payload: {
        annotation
      }
    }
  }

}
